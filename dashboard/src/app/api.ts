const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084';

export interface DataLakeHealth {
  status: string;
  service: string;
}

export interface DataLakeRoot {
  message: string;
}

export async function testDataLakeConnection(): Promise<DataLakeHealth> {
  try {
    const response = await fetch(`${API_BASE_URL}/healthz`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to connect to DataLake:', error);
    throw error;
  }
}

export async function getDataLakeRoot(): Promise<DataLakeRoot> {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to get DataLake root:', error);
    throw error;
  }
}
