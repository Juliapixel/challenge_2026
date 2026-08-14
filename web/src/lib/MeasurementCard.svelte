<script lang="ts">
    import favicon from "$lib/assets/favicon.svg";
    import PinIcon from "@iconify-svelte/material-symbols/location-on-outline";
    import ShapesIcon from "@iconify-svelte/material-symbols/shapes";
    import { Collapsible } from "bits-ui";
    import type { Snippet } from "svelte";
    import { slide } from "svelte/transition";

    interface Props {
        icon?: string;
        title: string;
        subtitle?: string;
        description?: string;
        children?: Snippet;
        open?: boolean;
    }

    let {
        icon,
        title,
        subtitle,
        description,
        children,
        open = $bindable(false)
    }: Props = $props();

    console.log(favicon);
</script>

<Collapsible.Root bind:open>
    <Collapsible.Trigger class="contents cursor-pointer">
        <div
            class="flex flex-row justify-between p-2 border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-500/20 md:p-4"
        >
            <div
                class="flex w-fit flex-row items-center gap-x-2 align-middle md:gap-x-4"
            >
                {#if icon}
                    <img
                        src={icon}
                        alt="Ícone da ocorrência"
                        class="h-18 w-18 rounded-2xl bg-zinc-300 object-cover md:h-24 md:w-24 dark:bg-zinc-700"
                    />
                {:else}
                    <ShapesIcon
                        class="h-18 w-18 rounded-2xl bg-zinc-300 object-cover p-2 text-zinc-100 md:h-24 md:w-24 dark:bg-zinc-700 dark:text-zinc-500"
                    />
                {/if}
                <div class="text-start leading-none">
                    <p
                        class="line-clamp-1 text-lg leading-normal font-semibold md:text-2xl"
                    >
                        {title}
                    </p>
                    <p
                        class="line-clamp-1 text-sm leading-none text-zinc-700 md:text-lg dark:text-zinc-400"
                    >
                        {subtitle}
                    </p>
                    <p class="text-md line-clamp-1 leading-normal md:text-xl">
                        {description}
                    </p>
                </div>
            </div>
            <div class="mr-4 flex flex-col self-center">
                <PinIcon class="h-8" />
                <p class="text-sm text-zinc-700 dark:text-zinc-300">NaN Km</p>
            </div>
        </div>
    </Collapsible.Trigger>
    <Collapsible.Content forceMount>
        {#snippet child({ open })}
            {#if open}
                <div transition:slide>
                    {@render children?.()}
                </div>
            {/if}
        {/snippet}
    </Collapsible.Content>
</Collapsible.Root>
