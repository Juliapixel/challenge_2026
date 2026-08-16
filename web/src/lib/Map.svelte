<script lang="ts">
    import { setOptions, importLibrary } from "@googlemaps/js-api-loader";
    import { mount, onMount } from "svelte";
    import Pin, { type PinKind } from "./Pin.svelte";
    import * as env from "$env/static/public";

    let mapElement: HTMLDivElement;

    interface Props {
        key: string;
        mapOptions: google.maps.MapOptions;
    }

    const { key, mapOptions }: Props = $props();

    onMount(async () => {
        setOptions({ key, authReferrerPolicy: "origin" });

        const [maps, marker, geocoding] = await Promise.all([
            importLibrary("maps"),
            importLibrary("marker"),
            importLibrary("geocoding")
        ]);

        // TODO: placeholder
        const geocoder = new geocoding.Geocoder();
        const pos = await geocoder.geocode({
            address: "FIAP Avenida Paulista"
        });
        const center = pos.results[0].geometry.location;

        const map = new maps.Map(mapElement, {
            ...mapOptions,
            center,
            mapId: env.PUBLIC_MAIN_MAP_ID,
            colorScheme: window.matchMedia("(prefers-color-scheme: dark)")
                .matches
                ? google.maps.ColorScheme.DARK
                : google.maps.ColorScheme.LIGHT
        });

        await new Promise<void>((res) => {
            google.maps.event.addListenerOnce(map, "idle", () => {
                res();
                // Run this code only after the map has loaded.
                console.log("The map is now ready!");
            });
        });

        // TODO: placeholder
        for (let i = 0; i < 10; i++) {
            let div = document.createElement("div");
            let kind: PinKind = (["ok", "warning", "critical"] as PinKind[])[
                Math.floor(Math.random() * 3)
            ];
            mount(Pin, {
                target: div,
                props: { kind }
            });
            new marker.AdvancedMarkerElement({
                content: div,
                position: {
                    lat: center.lat() + 0.001 * i,
                    lng: center.lng() + 0.001 * i
                },
                map,
                gmpClickable: true
            });
        }
    });
</script>

<div bind:this={mapElement} class="h-full w-full"></div>
