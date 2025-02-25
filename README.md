# Using AWS Copilot to deploy to Fargate using Amazon Cognito for authentication.

This repo represents the collection of my effort to deploy a simple python application to AWS Fargate with a public page and a private page.  The private page can be accessed after registration and authentication with Amazon Cognito.   The application uses AWS copilot as a tool to create all the AWS infrastructure needed and manage the deployment.   

Future updates will include:
  - the addition of a CI/CD pipeline using AWS CodePipeline.
  - the addition of a login page using Amazon Cognito.
  - the use of other OIDC providers for authentication like Facebook, Google, and Amazon

If you find this useful, I would appreciate you starring the repo.  If you have any questions, please feel free to reach out to me at [LinkedIn](https://www.linkedin.com/in/johnlafata)

## build locally
docker build . -t  python-web 

## test locally 

( should be able to get to the main page only unless you setup copilot manually to use the following )
 - localhost/authorize as redirect url and 
 - localhost/logout as logout url)
 - also set USER_POOL_ID and USER_POOL_CLIENT_ID in an .env 

```
docker run --name=python-web --rm -p 8080:8080 python-web
```
### prerequisites
- ensure that you have an ECR registry in AWS
- AWS CLI installed
- Docker Desktop installed
- AWS copilot installed
- non root account AWS_ACCESS_KEY and AWS_ACCESS_KEY_SECRET in AWS Profile
  - instructions: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html 
  - for example: create an alternate IAM user via the console, 
```
export AWS_PROFILE=my-app
```

### Usage
These are the basic stages to fargate deployment with AWS copilot

`copilot init` to create the app

`copilot svc init` to create the service

`copilot env init` to create the environment

`copilot app deploy` to deploy the app to the environment

You can pass the parameters in the command line if you want as follows, when prompted to create the environment, say no.

  ```
  copilot app init                   \
    python-web                       \
    --domain       'k8s-kloud.com'           
  ```

Response:
  ```
 Proposing infrastructure changes for stack python-web-infrastructure-roles
- Creating the infrastructure for stack python-web-infrastructure-roles                         [create complete]  [79.2s]
  - A StackSet admin role assumed by CloudFormation to manage regional stacks                   [create complete]  [18.6s]
  - Add NS records to delegate responsibility to the python-web.k8s-kloud.com subdomain         [create complete]  [31.0s]
  - A hosted zone for python-web.k8s-kloud.com                                                  [create complete]  [42.4s]
  - A DNS delegation role to allow accounts: 375559983734 to manage your domain                 [create complete]  [19.7s]
  - An IAM role assumed by the admin role to create ECR repositories, KMS keys, and S3 buckets  [create complete]  [19.5s]
✔ The directory copilot will hold service manifests for application python-web.

```


after the domain is initialized. You can associate the deployment information

``` 
  copilot init                                   \
    --app          python-web                    \
    --name         backend                       \
    --type         'Load Balanced Web Service'   \
    --dockerfile   './Dockerfile'                \
    --port         8080                          \
    --tag          '1.1.0'
```

Response:
  ```
  Note: It's best to run this command in the root of your Git repository.
  Welcome to the Copilot CLI! We're going to walk you through some questions
  to help you get set up with a containerized application on AWS. An application is a collection of
  containerized services that operate together.

  Ok great, we'll set up a Load Balanced Web Service named doc-processor in application doc-processor.

  ✔ Proposing infrastructure changes for stack doc-processor-infrastructure-roles
  - Creating the infrastructure for stack doc-processor-infrastructure-roles                           [create complete]  [44.2s]
    - A StackSet admin role assumed by CloudFormation to manage regional stacks                   [create complete]  [19.4s]
    - An IAM role assumed by the admin role to create ECR repositories, KMS keys, and S3 buckets  [create complete]  [17.3s]
  ✔ The directory copilot will hold service manifests for application doc-processor.

  Note: Architecture type arm64 has been detected. We will set platform 'linux/x86_64' instead. If you'd rather build and run as architecture type arm64, please change the 'platform' field in your workload manifest to 'linux/arm64'.
  ✔ Wrote the manifest for service doc-processor at copilot/doc-processor/manifest.yml
  Your manifest contains configurations like your container size and port.

  - Update regional resources with stack set "doc-processor-infrastructure"  [succeeded]  [0.0s]
  All right, you're all set for local development.
  Deploy: No

  No problem, you can deploy your service later:
  - Run `copilot env init` to create your environment.
  - Run `copilot deploy` to deploy your service.
  - Be a part of the Copilot ✨community✨!
    Ask or answer a question, submit a feature request...
    Visit 👉 https://aws.github.io/copilot-cli/community/get-involved/ to see how!
  ```


### create environment

Use the appropriate AWS Profile for your configuration in the following

  ```
  copilot env init              \
    --app 'python-web'            \
    --name 'qa'                  \
    --profile 'fargate-sandbox'         \
    --container-insights          \
    --default-config
  ```
Response:
  ```
  ✔ Manifest file for environment qa already exists at copilot/environments/qa/manifest.yml, skipping writing it.
  - Update regional resources with stack set "python-web-infrastructure"  [succeeded]  [1.7s]
  - Update regional resources with stack set "python-web-infrastructure"  [succeeded]           [39.0s]
    - Update resources in region "us-east-1"                              [create complete]     [38.0s]
      - KMS key to encrypt pipeline artifacts between stages              [create complete]     [18.6s]
      - S3 Bucket to store local artifacts                                [create in progress]  [1.0s]
  ✔ Proposing infrastructure changes for the python-web-qa environment.
  - Creating the infrastructure for the python-web-qa environment.  [create complete]  [42.7s]
    - An IAM Role for AWS CloudFormation to manage resources        [create complete]  [21.0s]
    - An IAM Role to describe resources in your environment         [create complete]  [19.3s]
  ✔ Provisioned bootstrap resources for environment qa in region us-east-1 under application python-web.
  Recommended follow-up actions:
    - Update your manifest copilot/environments/qa/manifest.yml to change the defaults.
    - Run `copilot env deploy --name qa` to deploy your environment.  ```
  ```

## deploy the env, the --no-rollback is useful to help debug any problems if it fails, but it's optional

  ```
  copilot env deploy      \
    --app python-web        \
    --name qa              \
    --no-rollback
  ```
Response:
  ```
  ✔ Proposing infrastructure changes for the python-web-qa environment.
  - Creating the infrastructure for the python-web-qa environment.                       [update complete]  [130.4s]
    - An ECS cluster to group your services                                              [create complete]  [3.7s]
    - An IAM role to manage certificates and Route53 hosted zones                        [create complete]  [15.4s]
    - Delegate DNS for environment subdomain                                             [create complete]  [36.5s]
    - A Route 53 Hosted Zone for the environment's subdomain                             [create complete]  [40.4s]
    - A security group to allow your containers to talk to each other                    [create complete]  [5.7s]
    - Request and validate an ACM certificate for your domain                            [create complete]  [40.8s]
    - An Internet Gateway to connect to the public internet                              [create complete]  [15.4s]
    - A resource policy to allow AWS services to create log streams for your workloads.  [create complete]  [3.0s]
    - Private subnet 1 for resources with no internet access                             [create complete]  [2.8s]
    - Private subnet 2 for resources with no internet access                             [create complete]  [2.8s]
    - A custom route table that directs network traffic for the public subnets           [create complete]  [9.3s]
    - Public subnet 1 for resources that can access the internet                         [create complete]  [2.9s]
    - Public subnet 2 for resources that can access the internet                         [create complete]  [2.9s]
    - A private DNS namespace for discovering services within the environment            [create complete]  [44.3s]
    - A Virtual Private Cloud to control networking of your AWS resources                [create complete]  [9.3s]
  ✔ Successfully deployed environment qa                                
  ```

### deploy the app

  ```
  copilot  deploy         \
    --app   python-web      \
    --name  backend      \
    --env   qa            \
    --tag   '1.1.0'        
  ```
Response:
  ```
  Checking for all required information. We may ask you some questions.
  Login Succeeded
  [+] Building 0.5s (10/10) FINISHED                                                                                      docker:desktop-linux
  => [internal] load build definition from Dockerfile                                                                                    0.0s
  => => transferring dockerfile: 781B                                                                                                    0.0s
  => [internal] load metadata for public.ecr.aws/docker/library/python:3.13.1-slim-bookworm                                              0.5s
  => [internal] load .dockerignore                                                                                                       0.0s
  => => transferring context: 2B                                                                                                         0.0s
  => [1/5] FROM public.ecr.aws/docker/library/python:3.13.1-slim-bookworm@sha256:031ebf3cde9f3719d2db385233bcb18df5162038e9cda20e64e08f  0.0s
  => [internal] load build context                                                                                                       0.0s
  => => transferring context: 66B                                                                                                        0.0s
  => CACHED [2/5] WORKDIR /app                                                                                                           0.0s
  => CACHED [3/5] RUN pip install -U gradio gradio_modal langchain langchain-openai logging llama_index llama-index llama-index-readers  0.0s
  => CACHED [4/5] COPY document-processor.py ./app.py                                                                                    0.0s
  => CACHED [5/5] COPY .env ./.env                                                                                                       0.0s
  => exporting to image                                                                                                                  0.0s
  => => exporting layers                                                                                                                 0.0s
  => => writing image sha256:668a86db0c18f4e7f51018da167bb3e18d92b778989596de94a1be958f1a9541                                            0.0s
  => => naming to 375559983734.dkr.ecr.us-east-1.amazonaws.com/python-web/backend:latest
  => => naming to 375559983734.dkr.ecr.us-east-1.amazonaws.com/python-web/backend:1.0.0                                         0.0s

  What's next:
      View a summary of image vulnerabilities and recommendations → docker scout quickview 
  The push refers to repository [375559983734.dkr.ecr.us-east-1.amazonaws.com/python-web/backend]
  43b236f75abb: Pushed 
  5efb54d9d7cc: Pushed 
  d7121cc7545f: Pushed 
  e096d71b6cb0: Pushed 
  c3185afbe4ae: Pushed 
  b75b92ab4865: Pushed 
  a0653a4a46ce: Pushed 
  7914c8f600f5: Pushed 
  lapython-web: digest: sha256:217dca0ca8f2669b60acc1a4386ef7393fd2a89fb421ca9f10129dbcf443286f size: 1993
  The push refers to repository [375559983734.dkr.ecr.us-east-1.amazonaws.com/python-web/backend]
  43b236f75abb: Layer already exists 
  5efb54d9d7cc: Layer already exists 
  d7121cc7545f: Layer already exists 
  e096d71b6cb0: Layer already exists 
  c3185afbe4ae: Layer already exists 
  b75b92ab4865: Layer already exists 
  a0653a4a46ce: Layer already exists 
  7914c8f600f5: Layer already exists 
  1.0.0: digest: sha256:217dca0ca8f2669b60acc1a4386ef7393fd2a89fb421ca9f10129dbcf443286f size: 1993
  ✔ Proposing infrastructure changes for stack python-web-qa-backend
    - Creating the infrastructure for stack python-web-qa-backend                   [create complete]  [426.5s]
    - Service discovery for your services to communicate within the VPC                    [create complete]  [0.0s]
    - Update your environment's shared resources                                           [update complete]  [208.2s]
      - An Elastic IP for NAT Gateway 2                                                    [create complete]  [14.2s]
      - An Elastic IP for NAT Gateway 1                                                    [create complete]  [18.3s]
      - A CloudFormation nested stack for your additional AWS resources                    [update complete]  [0.0s]
      - A security group for your load balancer allowing HTTP traffic                      [create complete]  [6.2s]
      - An Application Load Balancer to distribute public traffic to your services         [create complete]  [184.5s]
      - NAT Gateway 2 enabling workloads placed in private subnet 2 to reach the internet  [create complete]  [99.0s]
      - NAT Gateway 1 enabling workloads placed in private subnet 1 to reach the internet  [create complete]  [93.3s]
      - A load balancer listener to route HTTP traffic                                     [create complete]  [3.2s]
    - An IAM role to update your environment stack                                         [create complete]  [15.8s]
    - An IAM Role for the Fargate agent to make AWS API calls on your behalf               [create complete]  [15.8s]
    - An HTTP listener rule for path `/` that forwards HTTP traffic to your tasks          [create complete]  [0.0s]
    - A custom resource assigning priority for HTTP listener rules                         [create complete]  [4.1s]
    - A CloudWatch log group to hold your service logs                                     [create complete]  [8.1s]
    - An IAM Role to describe load balancer rules for assigning a priority                 [create complete]  [15.8s]
    - An ECS service to run and maintain your tasks in the environment cluster             [create complete]  [164.8s]
      Deployments                                                                                             
                Revision  Rollout      Desired  Running  Failed  Pending                                              
        PRIMARY  4         [completed]  1        1        0       0                                                    
    - A target group to connect the load balancer to your service on port 7860             [create complete]  [15.8s]
    - An ECS task definition to group your containers and run them on ECS                  [create complete]  [4.1s]
    - An IAM role to control permissions for the containers in your tasks                  [create complete]  [15.8s]
  ✔ Deployed service doc-processor.
  Recommended follow-up action:
    - Your service is accessible at https://backend.qa.python-web.k8s-kloud.com over the internet.

  ```

### logs
  ``` 
  copilot svc logs --follow
  ```

### teardown
  ```
  copilot app delete --yes
  ```

### create a CI/CD pipeline in AWS CODEPIPELINE
copilot pipeline init
git add copilot
git commit -m "adds copilot"
copilot pipeline deploy


# setting up google as an identity provider
# https://docs.aws.amazon.com/cognito/latest/developerguide/google.html


### login page
# https://docs.aws.amazon.com/cognito/latest/developerguide/login-endpoint.html