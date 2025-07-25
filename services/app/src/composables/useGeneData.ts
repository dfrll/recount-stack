import axios from 'axios'

export function useGeneData() {

    async function fetchGene(projectId: string, startRow: number, endRow: number) {
        try {
            const res = await axios.get(`/api/project/${projectId}/gene`, {
                params: { start: startRow, end: endRow }
            })
            if (res.data.status == 'success') {
                return {
                    rows: res.data.table,
                    totalCount: res.data.totalCount
                }
            } else {
                return { rows: [], totalCount: 0 }
            }

        } catch (e) {
            console.error('Failed to fetch gene data:', e)
            return { rows: [], totalCount: 0 }
        }
    }

    return { fetchGene }
}
