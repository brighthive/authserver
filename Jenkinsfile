pipeline {
  agent any
  options {
      // Will set the build timeout at 5 minutes and disable concurrent builds.
      timeout(time: 5, unit: 'MINUTES')
      disableConcurrentBuilds()
  }
  triggers {
      // All builds will happen upon github push
      githubPush()
  }
  stages {
      /*
        Initialize all the pipline parameters and thresholds.
      */
      stage("Initialize") {
        steps {
          initialize()
        }
      }
      /*
        The pre checks will spit out all the pipeline envs and parameters (This stage is added for debugging within Jenkins).
      */
      stage("Pre-Checks") {
        steps {
          sh 'docker images'
        }
      }
      /*
        Will take the files from repo and will run them with a docker container at the root level. (If passes, will cache deps and destory container)
        If no database is required use the following for testing.
        ----------
        withDockerContainer(image: env.DOCKER_PYTHON_NAME, args: "-u root:root") {
          sh "python --version"
          sh "pip install --no-cache-dir pipenv"
          sh "pipenv install --dev"
          sh "pipenv run pytest"
        }
      */
      stage('Testing') {
        steps {
          script {
            docker.image(env.DOCKER_DB_IMAGE_NAME).withRun("-h ${env.POSTGRES_HOST} -e POSTGRES_USER=${env.POSTGRES_USER} -e POSTGRES_PASSWORD=${env.POSTGRES_PASSWORD}") { db ->
                docker.image(env.DOCKER_DB_IMAGE_NAME).inside("--link ${db.id}:db") {
                    sh '''
                      psql --version
                      export PGPASSWORD=${POSTGRES_PASSWORD}
                      export RETRIES=${RETRIES_DBPING_IN_SECONDS}
                      until psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
                        echo "Waiting for postgres server, $((RETRIES-=1)) remaining attempts..."
                        sleep 1
                      done
                      psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -c "CREATE DATABASE ${POSTGRES_DB_NAME}"
                    '''
                }
                docker.image(env.DOCKER_PYTHON_NAME).inside("-u root:root --link ${db.id}:db") {
                    sh "python --version"
                    sh "pip install --no-cache-dir pipenv"
                    sh "pipenv install --dev"
                    sh 'printenv'
                    sh "pipenv run pytest -s"
                }
              }
            }
        }
      }
  }
}

def initialize() {
    // Docker Defs
    env.DOCKER_DB_IMAGE_NAME = 'postgres:11.1'
    env.DOCKER_PYTHON_NAME = 'python:3.7-slim'
    // AWS ERC Parameters / Push Rules
    env.REGISTRY_NAME = ''
    env.REGISTRY_URI = ''
    env.BRANCH_IMAGE_BUILD_PUSH = ''
    env.BRANCH_ALLOW_DEPLOYMENT = ''
    env.SYSTEM_NAME = 'Jenkins'
    env.IS_JENKINS_TEST = '1'
    env.AWS_REGION = 'us-west-1'
    env.MAX_ENVIRONMENTNAME_LENGTH = 32
    // DB Configs
    env.POSTGRES_HOST = 'localhost'
    env.POSTGRES_POT = 5432
    env.RETRIES_DBPING_IN_SECONDS = 60
    env.POSTGRES_USER = 'test_user'
    env.POSTGRES_PASSWORD = 'test_password'
    env.POSTGRES_DB_NAME = 'authservice_test'
    // K8 Deployment Parameters
    env.K8_SERVER_SSH_KEY_NAME = ''
    env.K8_APP_NAME_SERVICE = ''
    env.K8_USERNAME = ''
    env.K8_HOST = ''
}
