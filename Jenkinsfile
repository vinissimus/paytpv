node {
    rocketSend channel: 'jenkins', message: 'Job Started'
    try {
        stage('Check') {
            cleanWs()
            checkout scm
        }

        stage('Build') {
            image = docker.build("paytpv:${env.BUILD_NUMBER}")
        }
        
        stage('Test') {
            image.inside() {
                sh "pytest tests/"
            }
        }
        rocketSend channel: 'jenkins', message: 'Job Success'
    } catch(e) {
        rocketSend channel: 'jenkins', message: 'Job Failed'
        throw e
    }
}