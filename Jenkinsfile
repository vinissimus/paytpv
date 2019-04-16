node {
    rocketSend channel: 'jenkins', message: 'Job Started'
    try {
        stage('Check') {
            cleanWs()
            checkout scm
        }

        stage('Build') {
            docker.build("paytpv:${env.BUILD_NUMBER}")
        }
        
        stage('Test') {
            image = "paytpv:${env.BUILD_NUMBER}"
            sh "docker run --rm ${image}"
        }
        rocketSend channel: 'jenkins', message: 'Job Success'
    } catch(e) {
        rocketSend channel: 'jenkins', message: 'Job Failed'
        throw e
    }
}

def credentials() {
    def credString = ""
    withCredentials([string(credentialsId: 'paytpv', variable: 'credentials')]){
        credentials = credentials.split('-');
        def MERCHANTCODE = credentials[0]
        def MERCHANTPASSWORD = credentials[1]
        def MERCHANTTERMINAL = credentials[2]
        credString = "-e MERCHANTCODE=${MERCHANTCODE} -e MERCHANTPASSWORD=${MERCHANTPASSWORD} -e MERCHANTTERMINAL=${MERCHANTTERMINAL}"
    }    
    return credString
}