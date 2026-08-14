<script lang="ts">
    import favicon from "$lib/assets/favicon.svg";
    import PinIcon from "@iconify-svelte/material-symbols/location-on-outline";

    interface Props {
        icon?: string;
        title: string;
        subtitle?: string;
        description?: string;
    }

    let { icon, title, subtitle, description }: Props = $props();

    console.log(favicon);
</script>

<div class="flex flex-row justify-between p-2 md:p-4">
    <div
        class="flex w-fit flex-row items-center gap-x-2 align-middle md:gap-x-4"
    >
        {#if icon}
            <img
                src={favicon}
                alt="Ícone da ocorrência"
                class="h-18 w-18 rounded-2xl bg-zinc-300 object-cover md:h-24 md:w-24 dark:bg-zinc-700"
            />
        {:else}
            <img
                src={favicon}
                alt="Ícone da ocorrência"
                class="h-18 w-18 rounded-2xl bg-zinc-300 object-cover md:h-24 md:w-24 dark:bg-zinc-700"
            />
        {/if}
        <div class="leading-none">
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
