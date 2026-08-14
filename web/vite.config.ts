import tailwindcss from "@tailwindcss/vite";
import adapter from "@sveltejs/adapter-static";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
    plugins: [
        tailwindcss(),
        sveltekit({
            compilerOptions: {
                // Force runes mode for the project, except for libraries. Can be removed in svelte 6.
                runes: ({ filename }) =>
                    filename.split(/[/\\]/).includes("node_modules")
                        ? undefined
                        : true
            },
            adapter: adapter({ precompress: true }),
            csp: {
                directives: {
                    "script-src": [
                        "self",
                        "wasm-unsafe-eval",
                        "blob:",
                        "*.googleapis.com"
                    ]
                },
                // must be specified with either the `report-uri` or `report-to` directives, or both
                reportOnly: {
                    "script-src": [
                        "self",
                        "https://*.googleapis.com",
                        "https://*.gstatic.com",
                        "*.google.com",
                        "*.googleusercontent.com",
                        "data:",
                        "wasm-unsafe-eval"
                    ],
                    "report-uri": ["/"],
                    "img-src": [
                        "self",
                        "*.gstatic.com",
                        "*.googleapis.com",
                        "data:",
                        "blob:"
                    ],
                    "frame-src": ["*.google.com"],
                    "connect-src": [
                        "self",
                        "https://*.googleapis.com",
                        "*.google.com",
                        "https://*.gstatic.com",
                        "data:",
                        "blob:"
                    ],
                    "font-src": ["https://fonts.gstatic.com"],
                    "style-src": [
                        "self",
                        "unsafe-inline",
                        "https://fonts.googleapis.com",
                        "data:",
                        "blob:"
                    ],
                    "worker-src": ["blob:", "wasm-unsafe-eval"]
                }
            }
        })
    ]
});
