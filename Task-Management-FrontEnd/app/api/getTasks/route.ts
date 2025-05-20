import axios from 'axios';

export async function GET(req:any) {
  const token = req.headers.get('authorization');
  if (!token) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
  }

  try {
    const response = await axios.get(process.env.API_BASE_URL!, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return Response.json(response.data);
  } catch (error:any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
}




// useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const token =localStorage.getItem('id_token')
  //       const res = await axios.get(base_api,
  //         {
  //           headers: {
  //             Authorization: `Bearer ${token}`,
  //           },
  //         })
  //       console.log('API response data:', res.data)
  //       setTasks(res.data.tasks || [])
  //     } catch (err: any) {
  //       setError(err.message || "Error fetching data")
  //     } finally {
  //       setLoading(false)
  //     }
  //   }

  //   fetchData()
  // }, [])
