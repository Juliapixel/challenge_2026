<script lang="ts">
    import InfoBadge from "./InfoBadge.svelte";
    import type { ComponentProps } from "svelte";

    interface Props {
        location: string;
        subtext?: string;
        cards?: ComponentProps<typeof InfoBadge>[];
    }

    let { location, subtext, cards }: Props = $props();
</script>

<div
    class="w-fit rounded-2xl from-zinc-800/10 to-zinc-800/30 p-4 md:bg-linear-to-b"
>
    <h1
        class="text-3xl font-bold text-shadow-lg text-stroke-3 text-stroke-black/40"
    >
        {location}
    </h1>
    <sub class="text-xl text-shadow-lg text-stroke-3 text-stroke-black/40"
        >{subtext}</sub
    >
    <div
        class="pointer-events-auto mt-2 flex flex-row gap-x-2 overflow-x-scroll"
    >
        {#each cards as card, i (i)}
            <InfoBadge {...card} />
        {/each}
    </div>
</div>
