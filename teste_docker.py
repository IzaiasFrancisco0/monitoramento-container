import docker


client = docker.from_env()


print("conexão  com docker estabelecida")

containers = client.containers.list(all=True)

print("\nContainers encontrados:")

for container in containers:
    print(
	f"Nome: {container.name} | "
        f"Status: {container.status} | "
	f"ID: {container.short_id}"

    )

client.close()
