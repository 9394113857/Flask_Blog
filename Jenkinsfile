pipeline {
    agent any

    environment {
        FLASK_APP = 'app.py'
        FLASK_ENV = 'development'  // Change to 'production' for deployment
        AWS_REGION = '<Your AWS Region>'
        EC2_INSTANCE_ID = '<Your EC2 Instance ID>'
        GIT_REPO = '<Your Flask Git Repository URL>'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: "${env.GIT_REPO}"
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'pytest'  // Add your test command here if applicable
            }
        }
        
        stage('Deploy') {
            steps {
                sh """
                ssh -i /path/to/your/key.pem ec2-user@${EC2_INSTANCE_ID}.compute.amazonaws.com '
                cd /path/to/your/application &&
                git pull origin main &&
                source flask-project-env/bin/activate &&
                pip install -r requirements.txt &&
                flask db upgrade &&
                sudo systemctl restart your-flask-app'
                """
            }
        }
    }
}
