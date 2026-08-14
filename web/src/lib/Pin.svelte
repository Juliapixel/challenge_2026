<script lang="ts">
    import { Popover } from "bits-ui";

    export type PinKind = "ok" | "warning" | "critical";

    interface Props {
        kind: PinKind;
    }

    let { kind }: Props = $props();
</script>

<Popover.Root>
    <Popover.Trigger
        class="flex h-16 w-16 items-center justify-center rounded-full border border-zinc-700 bg-zinc-800 text-white hover:cursor-pointer"
    >
        TESTE
    </Popover.Trigger>
    <Popover.Portal>
        <Popover.Content
            align="center"
            side="top"
            class="rounded-md bg-zinc-800"
        >
            <div>TESTEEE</div>
        </Popover.Content>
    </Popover.Portal>
</Popover.Root>
