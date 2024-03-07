# Hame infra

## Setup

Run these steps the first time.

1. Install [Terraform](https://terraform.io) and `aws cli`
2. Create an AWS access key and store it locally in a credentials file (
   see [AWS Configuration basics](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config)
   and [Where are the configuration settings stored](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
   for more info)
3. To manage existing instances, install [sops](https://github.com/getsops/sops) to decrypt encrypted variable files in the repository.

### Multi-factor authentication (MFA)

If you get a 403 error when running terraform despite having configured a valid AWS
access key, you may need to set up MFA. Install both AWS CLI and jq, and make sure you have `aws` and `jq` in path. Execute the `[get-mfa-vars.sh](https://gist.github.com/mvaaltola/0abced5790401f2454444fb2ffd4acc0)` script with your AWS arn and your MFA access code,
and finally run `. /tmp/aws-mfa-token` to temporarily set the correct MFA environment variables in your shell.

## Managing existing instances

To manage existing instances, decrypt `hame-dev.tfvars.enc.json` by running `sops -d hame-dev.tfvars.enc.json > hame-dev.tfvars.json`.

To make changes to instances, first check that your variables and current infra is up to date with terraform state:

```shell
terraform init
terraform plan --var-file hame-dev.tfvars.json
```

This should report that terraform state is up to date with infra and configuration. You may make changes to configuration or variables and run `terraform plan --var-file hame-dev.tfvars.json` again to check what your changes would mean to the infrastructure.

When you are sure that you want to change AWS infra, run

```shell
terraform apply --var-file hame-dev.tfvars.json
```

Please verify that the reported changes are desired, and respond `yes` to apply the changes to infrastructure. Please also commit the changes in terraform files to Github. If you want to save the changes to your variables to Github, encrypt the variables with `sops -e hame-dev.tfvars.json > hame-dev.tfvars.enc.json` and commit the encrypted file.

## Configuring new instances

1. To create a new instance of hame-ryhti, copy [hame.tfvars.sample.json](hame.tfvars.sample.json) to a new file called `hame-your-deployment.tfvars.json`.
2. Create an IAM user for CI/CD and take down the username and credentials. This can be used to configure CD deployment from Github. If CD is already configured, fill in existing user in `AWS_LAMBDA_USER` part in `hame-your-deployment.tfvars.json`. Fill credentials in Github secrets `AWS_LAMBDA_UPLOAD_ACCESS_KEY_ID` and `AWS_LAMBDA_UPLOAD_SECRET_ACCESS_KEY`.
3. Change the values in `hame-your-deployment.tfvars.json` as required. If you need to save your instance variables to Github, you may encrypt the file with `sops -e hame-your-deployment.tfvars.json > hame-your-deployment.tfvars.enc.json`. The encrypted file may safely be added to a public Github repository.
4. Create zip packages for the lambda functions by running `make build-lambda -C ..` (this
   has to be done only once since github actions can be configured to update functions).

## Deploying instances

To launch new instances, run the following commands:

```shell
terraform init
terraform apply --var-file hame-your-deployment.tfvars.json
```

Note: Setting up the instances takes a couple of minutes.

## Teardown of instances

Shut down and destroy the instances with `terraform destroy --var-file hame-your-deployment.tfvars.json`

## Manual interactions

You can interact with the lambda functions using the [Makefile](./Makefile).

> For example migrate the database with `make migrate-db`
