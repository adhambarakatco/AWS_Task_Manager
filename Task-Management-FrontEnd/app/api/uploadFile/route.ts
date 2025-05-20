import axios from 'axios';

const url=process.env.API_BASE_URL!
export async function POST(req:any) {
    const token = req.headers.get('authorization');
    const body = await req.json();
    const task_id=body['task_id']
    const file_name=body['file_name']
    if (!token) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
    }
    console.log("UPLOAD START")
    try {
      const response = await axios.post(`${url}/${task_id}/attachments`,{
        file_name:file_name
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      console.log("UPLOAD WORKS")
      return Response.json(response.data.upload_url);
    } catch (error:any) {
      return new Response(JSON.stringify({ error: error.message }), { status: 500 });
    }
  }