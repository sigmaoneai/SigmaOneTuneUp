#!/usr/bin/env python3
"""
AWS CDK Infrastructure for SigmaOne TuneUp Backend
"""

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_rds as rds,
    aws_logs as logs,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    Duration,
    CfnOutput
)
from constructs import Construct

class SigmaOneTuneUpStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self, "SigmaOneTuneUpVPC",
            max_azs=2,
            nat_gateways=1
        )

        # RDS Database
        db_secret = secretsmanager.Secret(
            self, "DatabaseSecret",
            description="Database credentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "postgres"}',
                generate_string_key="password",
                exclude_characters='"@/\\'
            )
        )

        database = rds.DatabaseInstance(
            self, "SigmaOneTuneUpDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            credentials=rds.Credentials.from_secret(db_secret),
            allocated_storage=20,
            storage_encrypted=True,
            backup_retention=Duration.days(7),
            deletion_protection=False,  # Set to True in production
            database_name="sigmaonetune"
        )

        # ECS Cluster
        cluster = ecs.Cluster(
            self, "SigmaOneTuneUpCluster",
            vpc=vpc,
            container_insights=True
        )

        # Application Load Balanced Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "SigmaOneTuneUpService",
            cluster=cluster,
            memory_limit_mib=1024,
            cpu=512,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("."),
                container_port=8000,
                environment={
                    "ENVIRONMENT": "production",
                    "HOST": "0.0.0.0",
                    "PORT": "8000",
                    "DEBUG": "false",
                    "LOG_LEVEL": "info"
                },
                secrets={
                    "DATABASE_URL": ecs.Secret.from_secrets_manager(
                        db_secret,
                        field="connectionString"
                    )
                },
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="SigmaOneTuneUp",
                    log_retention=logs.RetentionDays.ONE_WEEK
                )
            ),
            public_load_balancer=True,
            desired_count=2,
            health_check_grace_period=Duration.seconds(60)
        )

        # Allow Fargate service to connect to RDS
        database.connections.allow_from(
            fargate_service.service,
            ec2.Port.tcp(5432),
            "Allow Fargate to connect to RDS"
        )

        # Outputs
        CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
            description="Application Load Balancer DNS name"
        )
        
        CfnOutput(
            self, "WebhookURL",
            value=f"https://{fargate_service.load_balancer.load_balancer_dns_name}/api/v1/retellai/agent-level-webhook",
            description="RetellAI Webhook URL"
        )

# App
app = cdk.App()
SigmaOneTuneUpStack(app, "SigmaOneTuneUpStack")
app.synth() 