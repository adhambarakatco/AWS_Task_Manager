declare module 'aws-lambda' {
  export interface APIGatewayProxyEvent {
    body: string | null;
    headers: { [name: string]: string };
    httpMethod: string;
    path: string;
    pathParameters: { [name: string]: string } | null;
    queryStringParameters: { [name: string]: string } | null;
    requestContext: any;
    resource: string;
    stageVariables: { [name: string]: string } | null;
  }

  export interface APIGatewayProxyResult {
    statusCode: number;
    headers?: {
      [header: string]: string | number | boolean;
    };
    body: string;
  }
} 