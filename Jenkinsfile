node {
    rocketSend channel: 'jenkins', message: 'Job Started'
    try {
        stage('Build') {
            sh 'make test'
        }
        rocketSend channel: 'jenkins', message: 'Job Success'
    } catch(e) {
        rocketSend channel: 'jenkins', message: 'Job Failed'
        throw e
    }
}