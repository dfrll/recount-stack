import axios from 'axios'

export function useGeneData() {

    async function fetchGene(projectId: string, startRow: number, endRow: number) {
        console.log('[useGeneData] Fetching gene data for project:', projectId, 'rows:', startRow, '-', endRow)
        try {
            const res = await axios.get(`/api/project/${projectId}/gene`, {
                params: { start: startRow, end: endRow }
            })
            console.log('[useGeneData] API response:', res.data)
            if (res.data.status == 'success') {
                return {
                    rows: res.data.table,
                    totalCount: res.data.totalCount
                }
            } else {
                console.error('[useGeneData] API returned error status:', res.data)
                return { rows: [], totalCount: 0 }
            }

        } catch (e) {
            console.error('Failed to fetch gene data:', e)
            return { rows: [], totalCount: 0 }
        }
    }

    return { fetchGene }
}
