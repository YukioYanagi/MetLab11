FROM rust:1.75-alpine AS builder

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release

FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /app

COPY --from=builder /app/target/release/rust-app .

EXPOSE 9000

CMD ["./rust-app"]
