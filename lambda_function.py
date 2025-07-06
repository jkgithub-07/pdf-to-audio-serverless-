import json
import boto3
import io
import PyPDF2

s3 = boto3.client('s3')
polly = boto3.client('polly')

def lambda_handler(event, context):
    print("Event:", event) 

    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    document_key = event['Records'][0]['s3']['object']['key']
    
    # Download PDF
    file_obj = s3.get_object(Bucket=bucket_name, Key=document_key)
    file_content = file_obj['Body'].read()
    
    # Read PDF text
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    
    if not text.strip():
        raise Exception("No text extracted. Is it a scanned image PDF?")
    
    # Convert to speech
    response = polly.synthesize_speech(
        Text=text[:2999],  # Polly limit
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    
    audio_stream = response.get('AudioStream')
    
    
    output_key = document_key.rsplit('.', 1)[0] + '.mp3'
    s3.put_object(
        Bucket='<output-bucket-name>',
        Key=output_key,
        Body=audio_stream.read()
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Audio file {output_key} saved in pdf-audio-converted!')
    }
