# **Task Management System on AWS using CDK**
## Deployed Website Link: 
https://ec2-3-77-233-142.eu-central-1.compute.amazonaws.com
# Landing page 
![Screenshot 2025-05-19 185839](https://github.com/user-attachments/assets/71812a64-7135-451b-a35d-89ef3bd53896)

# Sign in
![image](https://github.com/user-attachments/assets/cb195069-9f18-4908-8c49-08f0e598204b)

# Sign up
![image](https://github.com/user-attachments/assets/16235b38-d331-46ff-9ef7-473ac4c29ddf)

# Dashboard
![image](https://github.com/user-attachments/assets/ed68e9d4-db99-4cc4-9a74-26364958d439)

# Create New Task
![image](https://github.com/user-attachments/assets/61b9d5de-f3ee-4ad6-9ecd-73f07f87b724)

# Task Details
![image](https://github.com/user-attachments/assets/818c11ad-033a-49bc-99cd-e44d71a92384)

# Edit Task
![image](https://github.com/user-attachments/assets/98f1fa59-f9f7-4e3e-bb00-f70fbcaff4ac)

## **Project Overview**

The **Task Management System** is a web-based application designed and implemented using **Amazon Web Services (AWS)**. The system allows users to sign up, log in, create tasks, update task statuses, attach files to tasks, and receive notifications for task updates. This application utilizes several AWS services, including **RDS**, **Lambda**, **API Gateway**, **CloudWatch**, **SQS**, **Cognito**, and **S3** to provide a fully functional, scalable, and secure task management solution.

## **AWS Architecture Diagram**
![Architecture](https://github.com/user-attachments/assets/8a320c37-a0fd-4ea2-9c30-8f9ea1e7abd3)

## **Frontend Overview**

The **frontend** of the **Task Management System** is built using **Next.js** and **TypeScript**. It provides a dynamic, responsive, and user-friendly interface for interacting with the backend services deployed on AWS. The frontend enables users to securely sign up, log in, create and manage tasks, and attach files, with a smooth and modern user experience.

- **Frontend Framework**: Next.js
- **Language**: TypeScript
- **Styling**: Tailwind CSS (for responsive and modern UI)
- **Authentication**: AWS Cognito (for user authentication)
- **API Integration**: Connected to the backend API Gateway via RESTful API calls

### **Key Features in the Frontend**
1. **Task Management**:
   - Create, update, delete, and view tasks with relevant details like title, description, due date, and priority.
   - Attach files to tasks via **Amazon S3** integration.

2. **User Authentication**:
   - Secure sign-up and login flow using **Amazon Cognito**.
   
3. **Responsive Design**:
   - Mobile-first, responsive design using **Tailwind CSS**.

## **Project Objectives**

- **Develop a fully functional task management application hosted on AWS**.
- **Implement secure user authentication** and resource access control using **Cognito**.
- **Utilize both relational and NoSQL databases** for data storage (MySQL/PostgreSQL for relational and DynamoDB for non-relational data).
- **Leverage serverless computing** for backend logic and API management via **Lambda** and **API Gateway**.
- **Monitor application performance** and handle asynchronous tasks effectively using **CloudWatch** and **SQS**.
- **Gain practical experience** in cloud architecture, security, and cost management on AWS.

## **AWS Services Utilized**

- **Amazon Cognito**: Manages user authentication and identity.
- **IAM (Identity and Access Management)**: Controls access to AWS resources securely.
- **EC2 (Elastic Compute Cloud)**: Hosts the web application within a **VPC**.
- **Amazon S3**: Stores task attachments and user-uploaded files.
- **Amazon DynamoDB**: Handles non-relational data like task metadata.
- **Amazon RDS**: Manages relational data such as user profiles and task relationships.
- **AWS Lambda**: Executes serverless backend logic for task operations.
- **API Gateway**: Provides RESTful APIs for the application.
- **Amazon CloudWatch**: Monitors performance and logs system activity.
- **Amazon SQS**: Processes asynchronous tasks like notifications.

## **Project Architecture**

1. **User Authentication**: 
   - Users access the system through a web interface, with **Cognito** handling sign-up, sign-in, and secure access control.
  
2. **Application Hosting**: 
   - The web application runs on **EC2 instances** deployed within a **VPC**.
  
3. **Data Storage**: 
   - **RDS** stores relational data (e.g., user profiles, task relationships).
   - **DynamoDB** manages non-relational task metadata for quick retrieval.
   - **S3** stores user-uploaded files and task attachments.
  
4. **Backend Logic and APIs**: 
   - **API Gateway** provides RESTful endpoints (e.g., `/tasks`, `/tasks/{id}`) for task operations.
   - **Lambda functions** process requests and manage data in **DynamoDB** and **RDS**.

5. **Asynchronous Processing**: 
   - **SQS** queues messages for background tasks such as sending email notifications when tasks are updated.
   - **CloudWatch** monitors the process, logging metrics and errors.

## **User Flow**

1. **Sign Up / Login**: Users sign up or log in via **Cognito**.
2. **Create Task**: The user creates a task through the web interface.
3. **API Gateway**: The request is routed to **API Gateway**, triggering a **Lambda** function.
4. **Task Data Storage**: The **Lambda** function saves task data to **DynamoDB** and relational details to **RDS**.
5. **Attachments**: If an attachment is included, it is uploaded to **S3**.
6. **Task Updates**: Upon task updates, **SQS** queues a notification message (e.g., for email delivery).
7. **Monitoring**: **CloudWatch** monitors the process, logging metrics and errors for analysis.

## **Project Requirements**

### **Networking and Hosting:**
- Configure a **VPC** with public and private subnets.
- Deploy **EC2 instances** in the public subnet to host the web application.

### **Security and Access Control:**
- Set up **IAM roles** for EC2 instances to securely access **S3**, **DynamoDB**, **RDS**, and other services.
- Implement **Cognito** for user authentication and management.

### **Data Management:**
- Use **RDS** to store relational data (e.g., user profiles, task relationships).
- Use **DynamoDB** for non-relational task metadata.
- Store task attachments in **S3**.

### **API and Backend Logic:**
- Create REST APIs with **API Gateway** for task CRUD operations.
- Develop **Lambda functions** to handle API requests and manage data in **DynamoDB** and **RDS**.

### **Asynchronous Tasks:**
- Implement **SQS** to queue and process notification messages for task updates.

### **Monitoring and Logging:**
- Configure **CloudWatch** to monitor **EC2 instances**, **Lambda functions**, and **API Gateway**.
- Set up dashboards and alerts for performance tracking and error detection.

## **Deliverables**

- **Functional Application**: A fully operational task management system deployed on AWS with all features implemented.
- **Documentation**:
  - **Architecture Diagram**: Visual representation of how AWS services interact.
  - **Setup Guide**: Step-by-step instructions for deploying the application on AWS.
  - **User Manual**: Instructions for using the task management system.
- **Presentation**: A slide presentation or report detailing design decisions, challenges encountered, and key takeaways.

## **How to Deploy**

1. **Install AWS CLI and CDK**: Make sure you have **AWS CLI** and **AWS CDK** installed.
2. **Clone the Repository**: Clone this repository to your local machine.
3. **Set Up AWS Credentials**: Ensure your AWS credentials are configured.
4. **Install Dependencies**: Run `npm install` to install necessary dependencies.
5. **Deploy the Stack**: Run `cdk deploy` to deploy the backend resources on AWS.
6. **Deploy Frontend**: Host the frontend using **S3** or **AWS Amplify** and update the API URL in the frontend code.

## **Frontend Integration**

- The frontend is built using **Next.js** and **TypeScript**.
- The frontend interacts with the **backend API Gateway** to perform operations like task creation, viewing tasks, editing tasks, and uploading files to **S3**.
- Use **environment variables** in your frontend to dynamically configure the backend API URL.

### **Frontend API Integration Example**:

```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function createTask(taskData) {
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(taskData),
  });

  const data = await response.json();
  return data;
}
```
## **Conclusion**

This **Task Management System** allows users to manage tasks effectively using a web interface and integrates tightly with **AWS services** for authentication, file storage, backend processing, and monitoring. The use of **AWS CDK** provides a scalable and easily maintainable infrastructure, ensuring the system can grow as needed.


