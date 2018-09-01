{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "CodePipeline for {{repository_name}}",
  "Parameters": {
    "Environment": {
      "Description": "The environment in which this stack lives",
      "Type": "String"
    },
    "Project": {
      "Description": "The project code which owns this stack",
      "Type": "String"
    },
	"ProjectDescription":{
	  "Description":"project description",
	  "Type":"String"
	},
    "DeploymentBucketName":{
      "Description":"Logging bucket",
      "Type": "String"
    },
	"Image":{
		"Description":"Docker image",
		"Type":"String"
	},
	"RepositoryName":{
		"Description":"CodeCommit Repository Name",
		"Type":"String"
	},
	"BranchName":{
		"Description":"CodeCommit Repository Branch Name",
		"Type":"String"
	},
	"BuildServiceRole":{
	    "Description":"Code pipeline build service role",
	    "Type":"String"
	},
	"Subnets": {
	    "Type": "CommaDelimitedList"
	},
	"SecurityGroups": {
	    "Type": "CommaDelimitedList"
	},
	"VpcId": {
	    "Type": "String"
	},
	"BuildProjectName":{
        "Type":"String"
	},
	"EnvCode": {
		  "Type": "String"
	},
	"BuildspecFile":{
        "Type":"String"
    }
  },
  "Resources": {

    "LogGroup": {
          "Type": "AWS::Logs::LogGroup",
          "DependsOn": "CodeBuildProject",
          "Properties": {
              "LogGroupName": {"Fn::Join": ["", ["/aws/codebuild/", {"Ref": "BuildProjectName"}]]},
              "RetentionInDays": 90
          }
      },

    "CodeBuildProject": {
			"Type": "AWS::CodeBuild::Project",
			"Properties": {
				"Name": {"Ref":"BuildProjectName"},
				"Description": {"Ref":"ProjectDescription"},
				"ServiceRole": { "Ref": "BuildServiceRole"},
				"Artifacts": {
					"Type": "CODEPIPELINE"
				},
                "VpcConfig": {
                    "VpcId" : {"Ref": "VpcId"},
                    "Subnets":{"Ref": "Subnets"},
                    "SecurityGroupIds":{"Ref": "SecurityGroups"}
                },
				"Environment": {
					"Type": "linuxContainer",
					"ComputeType": "BUILD_GENERAL1_SMALL",
					"Image": {"Ref":"Image"},
					"EnvironmentVariables": [
                        {
                            "Name": "pipeline_env",
                            "Value": {
                                "Ref": "EnvCode"
                            }
                        },
                        {
                            "Name": "EnvCode",
                            "Value": {
                                "Ref": "EnvCode"
                            }
                        }
                     ]
				},
				"Source": {
                    "BuildSpec": {"Ref":"BuildspecFile"},
                    "Type": "CODEPIPELINE"
				},
				"TimeoutInMinutes": 60,
				"Tags": [
				  {
					"Key": "Name",
					"Value": {
					  "Fn::Join": [
						"-",
						[
						  {
							"Ref": "AWS::StackName"
						  }
						]
					  ]
					}
				  }

				]
			}
		},
      "Pipeline": {
         "Type": "AWS::CodePipeline::Pipeline",
         "Properties": {
            "RoleArn": { "Ref": "BuildServiceRole"},
            "ArtifactStore": {
               "Type": "S3",
               "Location": {"Ref":"DeploymentBucketName"}
            },
            "Stages": [
               {
                  "Name": "Source",
                  "Actions": [
                    {
                      "Name": "SourceAction",
                      "ActionTypeId": {
                        "Category": "Source",
                        "Owner": "AWS",
                        "Version": "1",
                        "Provider": "CodeCommit"
                      },
                      "OutputArtifacts": [
                        {
                          "Name": "CodePipelineSourceOutputArtifact"
                        }
                      ],
                      "Configuration": {
                        "BranchName": {"Ref":"BranchName"},
                        "RepositoryName": {"Ref":"RepositoryName"}
                      },
                      "RunOrder": 1
                    }
                  ]
               },
                {
                    "Name": "Build",
                    "Actions": [{
                        "Name": "BuildAction",
                        "InputArtifacts": [{
                            "Name": "CodePipelineSourceOutputArtifact"
                        }],
                        "ActionTypeId": {
                            "Category": "Build",
                            "Owner": "AWS",
                            "Version": 1,
                            "Provider": "CodeBuild"
                        },
                        "Configuration": {
                            "ProjectName": {
                                "Ref": "CodeBuildProject"
                            }
                        },
                        "OutputArtifacts": [{
                            "Name": "CodePipelineBuildOutputArtifact"
                        }],
                        "RunOrder": 1
                    }]
                }
            ]
         }
      }
  }
}