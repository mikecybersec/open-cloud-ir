# open-cloud-ir

A repository to store tooling and scripts I've created for cloud incident response.

## AWS Folder
This currently contains:
- genpreurl.py - This is a PoC python script that generates a presigned URL for a given AWS S3 bucket. This will later be absorbed into the wider project, but for now acts as a standalone script. The output URL can be used in 'collector.py' or the compiled version 'collector' as an input argument, telling the collector binary where to upload the forensics collection to.</br>
- collector.py - This is the main tool, it gathers and zips key forensics artefacts for Linux systems. Note if you're performing forensics of AWS ECS/Fargate, you can use the compiled version, or compile it yourself. </br></br>
**Usage**: python3 collector.py <PresignedURL> </br>
**Compile Instructions**: pyinstaller --onefile collector.py
**Usage if compiled**: ./collector <PresignedURL>
