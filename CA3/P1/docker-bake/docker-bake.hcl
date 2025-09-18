group "default" {
  targets = ["2048", "birthday"]
}

target "2048" {
  context = "./2048"
  dockerfile = "Dockerfile.2048"
  tags = ["myorg/app:latest"]
}

target "birthday" {
  context = "./birthday"
  dockerfile = "Dockerfile.birthday"
  tags = ["myorg/api:latest"]
}
