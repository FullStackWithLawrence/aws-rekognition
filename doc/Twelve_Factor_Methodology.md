# 12-Factor Methodology

This project conforms to [12-factor methodology](https://12factor.net/). We want to make this project more accessible to students and learners as an instructional tool while not adding undue code review workloads to anyone with merge authority for this project. To this end we've added several pre-commit code linting and code style tools as well as a quasi-standardized set of GitHub Actions CI/CD automations that manage pull requests and semantic releases.

- 1. **Codebase**: [✅] One codebase tracked in revision control, many deploys
- 2. **Dependencies**: [✅] Explicitly declare and isolate dependencies. We're using Terraform's built-in package lock, Python's requirements.txt, and Node's package.json to declare dependencies.
- 3. **Config**: [✅] Store config in the environment. This project implements a special [Settings](../terraform/python/rekognition_api/conf.py) class, which both validates and stores all configuration information for the package.
- 4. **Backing services**: [✅] Treat backing services as attached resources. We're persisting facial recognition indexes to AWS DynamoDB.
- 5. **Build, release, run**: [✅] Strictly separate build and run stages. `Build` is implemented in Makefile, `release` is implemented as a GitHub Action, and `run` is independently managed by AWS API Gateway.
- 6. **Processes**: [✅] Execute the app as one or more stateless processes. This REST API as well as the Lambda functions it calls are stateless.
- 7. **Port binding**: [✅] Export services via port binding. This micro service listens on ports 80 and 443.
- 8. **Concurrency**: [✅] Scale out via the process model. We achieve this "for free" since we're using AWS serverless infrastructure, which is inherently and infinitely scalable.
- 9. **Disposability**: [✅] Maximize robustness with fast startup and graceful shutdown. Terraform takes care of this for us. Running `terraform destroy` will completely remove this project and any residual data from your AWS account.
- 10. **Dev/prod parity**: [✅] Keep development, staging, and production as similar as possible. The GitHub Action [pushMain.yml](.github/workflows/pushMain.yml) executes a forced merge from main to dev branches. This ensure that all dev branches are synced to main immediately after pull requests are merged to main.
- 11. **Logs**: [✅] Treat logs as event streams. We get this "for free" by using AWS Cloudwatch.
- 12. **Admin processes**: [✅] Run admin/management tasks as one-off processes. All admin processes are implemented with GitHub Actions and other GitHub management features. The Terraform command lines services as our admin console for this API.
