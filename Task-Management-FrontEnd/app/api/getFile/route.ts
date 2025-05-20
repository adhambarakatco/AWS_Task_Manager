import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";


const access_key=process.env.AWS_ACCESS_KEY_ID || ""
const secret_access_key=process.env.AWS_SECRET_ACCESS_KEY || ""

const bucket_name=process.env.S3_BUCKET_NAME ||  ""
const s3Client = new S3Client({
    region: "eu-central-1", // e.g., "us-east-1"
    credentials: {
      accessKeyId: access_key, 
      secretAccessKey: secret_access_key,
    },
  });
  
  async function getS3ObjectUrl(bucketName: string, objectKey: string) {
    const command = new GetObjectCommand({
      Bucket: bucketName,
      Key: objectKey,
    });

    const url = await getSignedUrl(s3Client, command, { expiresIn: 3600 });
      return url;

}
export async function GET(req: Request) {
    try {
      const urlObj = new URL(req.url);
      const objectKey = urlObj.searchParams.get("object_Key");
      
      if (!objectKey) {
        return new Response(JSON.stringify({ error: "Missing object_Key parameter" }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        });
      }
  
      const url = await getS3ObjectUrl(bucket_name, objectKey);
  
      return new Response(
        JSON.stringify({ url }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      );
  
    } catch (error: any) {
      return new Response(
        JSON.stringify({ error: error.message }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }
  }
  
  