import json
import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:558372295124:deployPortfolioTopic')

    try:
      s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

      portfolio_bucket = s3.Bucket('portfolio.drhuggins.info')
      build_bucket = s3.Bucket('portfoliobuild.drhuggins.info')

      portfolio_zip = StringIO.StringIO()
      build_bucket.download_fileobj('buildPortfolio.zip', portfolio_zip)

      with zipfile.ZipFile(portfolio_zip) as myzip:
          for nm in myzip.namelist():
            obj = myzip.open(nm)
            portfolio_bucket.upload_fileobj(obj, nm,
              ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

      print "Job Done!"

      topic.publish(Subject="Your Portfolio Has Been Updated", Message="The portfolio has been deployed successfully.")
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="The Portfolio was not deployed successfully!")
        raise
