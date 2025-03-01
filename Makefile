.PHONY: all clean test rust go

all: build_dir rust go

build_dir:
	mkdir -p build

rust: build_dir
	cargo build
	cp target/debug/librevm_wrapper.dylib build/librevm_wrapper.so

go: build_dir
	cd wrappers/golang && go build -buildmode=c-shared -o ../../build/libgo_ethereum_wrapper.so go_ethereum_wrapper.go


test: go rust
	uv run pytest python/tests/ -vvvv -s 

clean:
	rm -rf build/*
	cargo clean
	rm -rf python/*.so python/__pycache__ python/*.c
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +