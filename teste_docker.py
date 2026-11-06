import docker

#conectar ao docker engine local
client = docker.from_env()

#verificar conexão
print("conexão  com docker estabelecida")

#listar containers
containers = client.containers.list(all=True)

print("\nContainers encontrados:")

for container in containers:
    print(
	f"Nome: {container.name} | "
        f"Status: {container.status} | "
	f"ID: {container.short_id}"

    )

client.close()
