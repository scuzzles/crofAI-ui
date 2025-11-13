<script lang="ts">
  import { onMount } from "svelte";
  import Layer from "./Layer.svelte";
  import { slide } from "svelte/transition";
  import { parse } from "./microdown";

  let temperature = $state(1);
  let model = $state("kimi-k2-0905");
  type Model = { id: string; name: string };
  let models: Model[] = $state([]);

  let prompt = $state("");
  type Generation = { reasoning: string; content: string; ttft?: number; tps?: number };
  let generation: Generation | undefined = $state();
  let aborter: AbortController | undefined = $state();

  const updateModels = async () => {
    const r = await fetch("/v2/models");
    if (!r.ok) {
      throw new Error(`Models are ${r.status}ing`);
    }
    const { data }: { data: Model[] } = await r.json();
    models = data.map((m) => {
      let name = m.name;
      if (m.id.endsWith("-turbo")) {
        name += " (Turbo)";
      }
      if (m.id.endsWith("-eco")) {
        name += " (Eco)";
      }
      if (m.id.endsWith("-reasoner")) {
        name += " (Reasoner)";
      }
      return { id: m.id, name };
    });
  };
  async function* iterateStream(stream: ReadableStream) {
    const reader = stream.getReader();
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) return;
        yield value;
      }
    } finally {
      reader.releaseLock();
    }
  }
  const send = async () => {
    const promptFixed = prompt.trim();
    if (!promptFixed) return;

    const start = Date.now();
    const r = await fetch("/v2/chat/completions", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model,
        temperature,
        messages: [
          {
            role: "user",
            content: promptFixed,
          },
        ],
        stream: true,
      }),
      signal: aborter!.signal,
    });
    if (!r.ok) {
      throw new Error(`Generation failed with status ${r.status}`);
    }

    let g: Generation = $state({ reasoning: "", content: "" });
    generation = g;

    let buffer = "";
    for await (const chunk of iterateStream(r.body!)) {
      buffer += new TextDecoder().decode(chunk);
      const parts = buffer.split("\n\n");
      buffer = parts.pop()!;
      for (const part of parts) {
        if (!part.startsWith("data: ")) continue;
        const data = part.slice(6).trim();
        if (data == "[DONE]") continue;
        const parsed = JSON.parse(data);

        const delta = parsed.choices[0].delta;
        if (delta) {
          const { reasoning_content, content } = delta;
          if (reasoning_content) g.reasoning += reasoning_content;
          if (content) g.content += content;
          if (reasoning_content?.trim() || content?.trim()) {
            g.ttft ||= Date.now() - start;
          }
        }

        if (parsed.usage) {
          g.tps = parsed.usage.tokens_per_second;
        }
      }
    }
  };
  const sendWrapped = async (e: SubmitEvent) => {
    e.preventDefault();
    aborter = new AbortController();
    try {
      await send();
    } finally {
      aborter = undefined;
    }
  };

  onMount(() => {
    updateModels();
  });
</script>

<div class="container">
  <div class="content">
    <form onsubmit={sendWrapped} class="prompt-container">
      <textarea
        placeholder="Prompt"
        bind:value={prompt}
        onkeydown={(e) => {
          if (e.key == "Enter" && (e.metaKey || e.ctrlKey)) {
            e.currentTarget.form?.requestSubmit();
          }
        }}
      ></textarea>
      <button disabled={Boolean(aborter)}>
        <Layer />
        Send
      </button>
    </form>
    {#if generation?.reasoning.trim()}
      <div class="output" in:slide={{ duration: 500 }}>
        <h2 class="font-title-medium">Reasoning</h2>
        <output class="prose">{@html parse(generation.reasoning)}</output>
      </div>
    {/if}
    {#if generation?.content.trim()}
      <div class="output" in:slide={{ duration: 500 }}>
        <h2 class="font-title-medium">Response</h2>
        <output class="prose">{@html parse(generation.content)}</output>
      </div>
    {/if}
  </div>
  <div class="sidebar">
    <select class="model-selector" bind:value={model}>
      {#each models as m}
        <option value={m.id}>{m.name}</option>
      {/each}
    </select>
    <label>
      <p>
        <span>Temperature</span>
        <output>{temperature.toFixed(1)}</output>
      </p>
      <input type="range" min="0" max="2" step="any" bind:value={temperature} />
    </label>
    {#if generation?.ttft || generation?.tps}
      <div class="stats">
        <h3 class="font-title-medium">Stats</h3>
        {#if generation?.ttft}
          <p>TTFT: <output>{(generation.ttft / 1000).toFixed(2)}s</output></p>
        {/if}
        {#if generation?.tps}
          <p><output>{generation.tps.toFixed(0)}</output> TPS</p>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .container {
    display: grid;
    grid-template-columns: 1fr 20rem;
    flex-grow: 1;
    gap: 0.5rem;
    padding: 0.5rem;
  }
  .content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    > * {
      flex: 1;
    }
  }
  .prompt-container {
    display: grid;
    position: relative;
    min-height: 20dvh;
    textarea {
      resize: none;
      padding: 0.5rem 1rem;
      border-radius: 1rem;
      box-shadow: inset 0 0 0 1px rgb(var(--m3-scheme-outline));
      &:focus {
        outline: none;
        box-shadow: inset 0 0 0 2px rgb(var(--m3-scheme-secondary));
      }
    }
    button {
      display: flex;
      height: 2rem;
      border-radius: 1rem;
      align-items: center;
      padding-inline: 1rem;

      position: absolute;
      bottom: 0;
      right: 0;

      background-color: rgb(var(--m3-scheme-primary));
      color: rgb(var(--m3-scheme-on-primary));
      transition:
        background-color 200ms,
        color 200ms;
      &:disabled {
        opacity: 0.38;
      }
      &:enabled {
        cursor: pointer;
      }
    }
  }
  .output {
    display: flex;
    flex-direction: column;
    padding: 0.5rem;
    border-radius: 1rem;
    background-color: rgb(var(--m3-scheme-surface-container));
  }

  .sidebar {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  select {
    height: 2rem;
    padding-inline: 1rem;
    border-radius: 1rem;
    box-shadow: inset 0 0 0 1px rgb(var(--m3-scheme-outline));
    cursor: pointer;
  }
  label {
    display: flex;
    flex-direction: column;
    p {
      display: flex;
      justify-content: space-between;
      margin: 0;
    }
    output {
      color: rgb(var(--m3-scheme-on-surface-variant));
    }
  }
  .stats {
    padding: 0.5rem;
    border-radius: 1rem;
    margin-top: auto;
    background-color: rgb(var(--m3-scheme-primary-container-subtle));
    color: rgb(var(--m3-scheme-on-primary-container-subtle));
  }
</style>
