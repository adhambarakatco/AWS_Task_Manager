from aws_cdk import (
    aws_cognito as cognito,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    CfnOutput,
    Stack,
    Aws
)
from constructs import Construct


class CognitoConstruct(Construct):
    def __init__(
            self,
            scope: Construct,
            id: str,
            **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        # Create User Pool
        self.user_pool = cognito.UserPool(
            self, "TaskManagerUserPool",
            mfa=cognito.Mfa.OPTIONAL,
            mfa_second_factor=cognito.MfaSecondFactor(
              sms=True,
              otp=True
            ),
            self_sign_up_enabled=True,
            auto_verify={"email": True},
            standard_attributes=cognito.StandardAttributes(
              email=cognito.StandardAttribute(required=True, mutable=True),
              given_name=cognito.StandardAttribute(required=True, mutable=True),
              family_name=cognito.StandardAttribute(required=True, mutable=True)
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Add standard attributes required for the application
        self.user_pool_client = self.user_pool.add_client(
            "app-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    implicit_code_grant=True
                ),
                scopes=[cognito.OAuthScope.EMAIL, cognito.OAuthScope.OPENID, cognito.OAuthScope.PROFILE],
                callback_urls=["http://localhost:3000/callback"]
            )
        )
       

        self.domain = self.user_pool.add_domain(
            "CognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="task-master-app-dev"
            )
        )

        # Create Identity Pool (allows unauthenticated and authenticated access)
        self.identity_pool = cognito.CfnIdentityPool(
            self, "TaskManagerIdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.user_pool_client.user_pool_client_id,
                    provider_name=f"cognito-idp.{Aws.REGION}.amazonaws.com/{self.user_pool.user_pool_id}"
                )
            ]
        )

        # Create authenticated role
        self.authenticated_role = iam.Role(
            self, "CognitoAuthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                {
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                },
                "sts:AssumeRoleWithWebIdentity"
            )
        )

        # Create role mapping
        cognito.CfnIdentityPoolRoleAttachment(
            self, "IdentityPoolRoleAttachment",
            identity_pool_id=self.identity_pool.ref,
            roles={
                "authenticated": self.authenticated_role.role_arn
            }
        )

        # Output user pool ID for reference
        CfnOutput(
            self, "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="The ID of the Cognito User Pool"
        )

        # Output client ID for reference
        CfnOutput(
            self, "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="The ID of the Cognito User Pool Client"
        )

        # Output Identity Pool ID for reference
        CfnOutput(
            self, "IdentityPoolId",
            value=self.identity_pool.ref,
            description="The ID of the Cognito Identity Pool"
        )