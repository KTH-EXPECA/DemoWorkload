client_img := 'expeca/primeworkload:client'
server_img := 'expeca/primeworkload:server'
client_dockerfile := 'Dockerfile.client'
server_dockerfile := 'Dockerfile.server'

docker_user := 'expeca'
docker_pass := 'ExPECAEdgeComputing@KTH'

.PHONY : containers _build_and_push_client _build_and_push_server _login _logout _buildx_support

containers : _logout

_buildx_support :
	docker run --privileged --rm tonistiigi/binfmt --install arm64,riscv64,arm ,

_login : _buildx_support
	docker login -u ${docker_user} -p ${docker_pass}

_logout : _build_and_push_client _build_and_push_server
	docker logout

_build_and_push_client : _login
	docker buildx build --platform linux/amd64,linux/arm64 -t ${client_img} -f ${client_dockerfile} . --push
	# docker push ${client_img}

_build_and_push_server : _login
	docker buildx build --platform linux/amd64,linux/arm64 -t ${server_img} -f ${server_dockerfile} . --push
	# docker push ${server_img}
