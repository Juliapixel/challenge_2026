<script lang="ts">
    import { env } from "$env/dynamic/public";
    import Map from "$lib/Map.svelte";
    import MapInfo from "$lib/MapInfo.svelte";
    import MeasurementCard from "$lib/MeasurementCard.svelte";
</script>

<div class="relative h-125 w-full p-0">
    <div
        class="pointer-events-none absolute top-0 z-10 h-16 w-full bg-linear-to-b from-black/20 to-transparent"
    ></div>
    <div
        class="pointer-events-none absolute bottom-0 z-10 w-full bg-linear-to-t from-black/20 to-transparent px-4 pt-8 pb-4 text-white"
    >
        <MapInfo
            location="Rodovia Coisa e Tal"
            subtext="Km 250"
            cards={[
                { kind: "warning", text: "Aviso" },
                { kind: "error", text: "Alerta" },
                { kind: "regular", text: "Info" }
            ]}
        />
    </div>

    <Map
        key={env.PUBLIC_GOOGLE_MAPS_API_KEY}
        mapOptions={{
            zoom: 15,
            cameraControl: true,
            styles: [
                {
                    featureType: "poi",
                    stylers: [
                        {
                            visibility: "off"
                        }
                    ]
                }
            ],
            fullscreenControl: false,
            mapTypeControl: false,
            streetViewControl: false
        }}
    />
</div>
<!-- TODO: placeholder -->
<div
    class="border-t border-zinc-200 dark:border-zinc-600 dark:bg-zinc-800 dark:text-white"
>
    <h2 class="border-b border-zinc-200 px-2 py-1 text-lg dark:border-zinc-600">
        Pontos de Monitoramento
    </h2>
    <MeasurementCard
        title="Rodovia seilaoq"
        subtitle="Km 200"
        description="Poda imediata"
    />
    <MeasurementCard
        title="Rodovia seilaoq"
        subtitle="Km 67"
        description="Poda em 1 semana"
    />
</div>
