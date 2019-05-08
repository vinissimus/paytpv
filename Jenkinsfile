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
            dev_credentials('credentials') {
                sh "docker run --rm ${credentials} ${image}"
            }
        }
        rocketSend channel: 'jenkins', message: 'Job Success'
    } catch(e) {
        rocketSend channel: 'jenkins', message: 'Job Failed'
        throw e
    }
}

def dev_credentials(variable, cl) {
    withCredentials([string(credentialsId: 'paytpv', variable: 'c')]){
        c = c.split('-');
        def MERCHANTCODE = c[0]
        def MERCHANTPASSWORD = c[1]
        def MERCHANTTERMINAL = c[2]
        def credentials = "-e MERCHANTCODE=${MERCHANTCODE} -e MERCHANTPASSWORD=${MERCHANTPASSWORD} -e MERCHANTTERMINAL=${MERCHANTTERMINAL}"

        withEnv(["${variable}=${credentials}"]) {
            cl()
        }
    }
}
