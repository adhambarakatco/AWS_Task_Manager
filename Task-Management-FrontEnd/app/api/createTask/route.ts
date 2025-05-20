import axios from 'axios';

export async function POST(req:any) {
  const token = req.headers.get('authorization');
  const body = await req.json();
  if (!token) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
  }
  console.log("CREATE START")
  try {
    const response = await axios.post(process.env.API_BASE_URL!,body, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    console.log("CREATE WORKS")
    return Response.json(response.data.task_id);
  } catch (error:any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
}