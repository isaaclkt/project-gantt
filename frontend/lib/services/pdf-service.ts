/**
 * PDF Export Service
 * Handles PDF file downloads from the backend
 */

import { API_BASE_URL } from '../api-config';

/**
 * Export a project to PDF
 *
 * @param projectId - The project ID to export
 * @returns Promise resolving to true on success
 * @throws Error if export fails
 */
export async function exportProjectToPDF(projectId: string): Promise<boolean> {
  const url = `${API_BASE_URL}/projects/${projectId}/export/pdf`;

  try {
    // Get auth token
    const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
    if (!token) {
      throw new Error('Token de autenticação não encontrado');
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Erro ao exportar PDF: ${response.status}`);
    }

    // Get the filename from the Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'project-report.pdf';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '');
      }
    }

    // Get the blob (PDF file)
    const blob = await response.blob();

    // Create download link and trigger download
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    return true;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Erro desconhecido ao exportar PDF');
  }
}
