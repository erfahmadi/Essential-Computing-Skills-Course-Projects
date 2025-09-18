FROM wasmedge/slim:0.13.4

COPY app.wasm /app.wasm

ENTRYPOINT ["/usr/local/bin/wasmedge", "/app.wasm"]
