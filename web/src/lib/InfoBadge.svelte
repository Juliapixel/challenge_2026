<script lang="ts">
    import type { HTMLAttributes } from "svelte/elements";
    import type IconComponent from "@iconify-svelte/material-symbols/types/gfwqskkx.d.js";
    import InfoIcon from "@iconify-svelte/material-symbols/info-outline";
    import WarningIcon from "@iconify-svelte/material-symbols/warning-outline";
    import ErrorIcon from "@iconify-svelte/material-symbols/error-outline";

    import { mount, onMount } from "svelte";

    export type CardKind = "regular" | "warning" | "error";

    type OptionalIcon =
        | {
              text: string;
              kind: CardKind;
              icon?: typeof IconComponent;
          }
        | {
              text: string;
              kind: undefined;
              icon: typeof IconComponent;
          };

    type Props = HTMLAttributes<HTMLDivElement> & OptionalIcon;

    const { text, kind, icon, ...props }: Props = $props();

    let [fillClass, defaultIcon] = $derived.by(() => {
        switch (kind) {
            case "warning":
                return ["dark:text-yellow-400 text-amber-500", WarningIcon];
            case "error":
                return ["dark:text-red-400 text-red-600", ErrorIcon];
            default:
                return ["text-black dark:text-white", InfoIcon];
        }
    });

    let iconElement: HTMLDivElement;
    onMount(() => {
        mount(icon ?? defaultIcon, {
            target: iconElement,
            props: { class: "h-6 w-6" }
        });
    });
</script>

<div
    {...props}
    class="flex w-fit flex-row items-center gap-x-1.5 rounded-xl border border-zinc-200 bg-zinc-100 py-2 pr-3 pl-2.5 select-none dark:border-zinc-600 dark:bg-zinc-800 {fillClass}"
>
    <div class="contents" bind:this={iconElement}></div>
    <span class="max-w-32 overflow-clip text-ellipsis whitespace-nowrap"
        >{text}</span
    >
</div>
