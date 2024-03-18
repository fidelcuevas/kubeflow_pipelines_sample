import kfp
import kfp.components as components
from kfp import compiler
from datetime import datetime
from kubernetes import client as k8s_client

RUN_TIME = datetime.today().replace(hour=5, minute=0, second=0).isoformat() #.strftime("%Y-%m-%d %H:%M:%S")
REGISTRY_SECRET_NAME = 'gitlab-registry-secret'

create_datalink = components.load_component_from_file('./components/etl/datalink.yaml')


def qis_daily_batch(date):
    datalink = create_datalink(date)


pipeline_conf = kfp.dsl.PipelineConf()
pipeline_conf.set_image_pull_secrets([k8s_client.V1ObjectReference(name=REGISTRY_SECRET_NAME)])
compiler.Compiler().compile(pipeline_func=qis_daily_batch, package_path='pipeline.yaml', pipeline_conf=pipeline_conf)

credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
client = kfp.Client(credentials=credentials)
client.upload_pipeline_version(pipeline_package_path='pipeline.yaml', pipeline_version_name=datetime.now().isoformat(), pipeline_name='QIS Daily', description='n/a')
client.create_recurring_run(experiment_id='25cb7d5a-9075-4bef-8ee3-2b0b4be5fd73', job_name='QIS Daily', cron_expression='0 5 * * *', pipeline_package_path='pipeline.yaml', params={'--date': "[[ScheduledTime.2006-01-02]]"})