client_img := 'expeca/echowkld:client'
server_img := 'expeca/echowkld:server'
client_dockerfile := 'Dockerfile.client'
server_dockerfile := 'Dockerfile.server'

docker_user := 'expeca'
docker_pass := 'ExPECAEdgeComputing@KTH'

.PHONY : containers _build_and_push_client _build_and_push_server _login _logout

containers : _logout

_login :
	docker login -u ${docker_user} -p ${docker_pass}

_logout : _build_and_push_client _build_and_push_server
	docker logout

_build_and_push_client : _login
	docker build -t ${client_img} -f ${client_dockerfile} .
	docker push ${client_img}

_build_and_push_server : _login
	docker build -t ${server_img} -f ${server_dockerfile} .
	docker push ${server_img}
