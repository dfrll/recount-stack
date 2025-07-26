<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, inject, watch, computed } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import { useVisibility } from '@/composables/useVisibility'
import { useProjectData } from '@/composables/useProjectData'
import { projectColumnDefs } from '@/columns/projectColumns'
import { useGeneData } from '@/composables/useGeneData'
import { geneColumnDefs } from '@/columns/geneColumns'
import { useExonData } from '@/composables/useExonData'
import { exonColumnDefs } from '@/columns/exonColumns'
import type { GridApi, IServerSideDatasource, Theme } from 'ag-grid-community'
import type { GridOptions } from 'ag-grid-enterprise'

const route = useRoute()
const mdTheme = inject<Theme<unknown>>('mdTheme');

// grid API instances
const projectGridApi = ref<GridApi | null>(null)
const geneGridApi = ref<GridApi | null>(null)
const exonGridApi = ref<GridApi | null>(null)

// composables for data fetching from backend APIs
const { project, fetchProject } = useProjectData()
const { fetchGene } = useGeneData()
const { fetchExon } = useExonData()

// visibility state and toggles for collapsible tables
const { isVisible: isProjectVisible, toggle: toggleProject } = useVisibility(true)
const { isVisible: isGeneVisible, toggle: toggleGene } = useVisibility(false)
const { isVisible: isExonVisible, toggle: toggleExon } = useVisibility(false)

// track which project IDs have already triggered insert logic
const insertedGeneProjects = ref<Set<string>>(new Set())
const insertedExonProjects = ref<Set<string>>(new Set())

// computed properties
const projectId = computed(() => route.params.project_id as string)

// server-side datasource for gene table
const geneDatasource: IServerSideDatasource = {
    getRows(params: any) {
        const { startRow, endRow } = params.request;
        const currentProjectId = projectId.value

        console.log('[GeneDatasource] Fetching rows:', { startRow, endRow, projectId: currentProjectId })

        if (!currentProjectId) {
            console.error('[GeneDatasource] No project ID available')
            params.fail()
            return
        }

        fetchGene(currentProjectId, startRow, endRow)
            .then(({ rows, totalCount }) => {
                console.log('[GeneDatasource] Success:', {
                    projectId: currentProjectId,
                    rowCount: rows?.length,
                    totalCount,
                    firstRowData: rows?.[0],
                })
                params.success({ rowData: rows, rowCount: totalCount })
            })
            .catch((error) => {
                console.error('[GeneDatasource] Error fetching data:', error)
                params.fail()
            })
    },
}

// server-side datasource for exon table
const exonDatasource: IServerSideDatasource = {
    getRows(params: any) {
        const { startRow, endRow } = params.request
        const currentProjectId = projectId.value

        console.log('[ExonDatasource] Fetchin rows:', { startRow, endRow, projectId: currentProjectId })

        if (!currentProjectId) {
            params.fail()
            return
        }

        fetchExon(currentProjectId, startRow, endRow)
            .then(({ rows, totalCount }) => {
                console.log('[ExonDatasource] Success:', { rows, totalCount })
                params.success({ rowData: rows, rowCount: totalCount })
            })
            .catch(error => {
                console.error('[ExonDatasource] Error:', error)
                params.fail()
            })
    },
}

// handlers
function onProjectGridReady(params: any) {
    projectGridApi.value = params.api
    console.log('[ProjectGrid] Grid ready');
}

function onGeneGridReady(params: any) {
    console.log('[GeneGrid] API methods:', Object.keys(params.api));
    geneGridApi.value = params.api
    params.api.setServerSideDatasource(geneDatasource)
    console.log('[GeneGrid] Grid ready');
}

function onExonGridReady(params: any) {
    exonGridApi.value = params.api
    params.api.setServerSideDatasource(exonDatasource)
    console.log('[ExonGrid] Grid ready');
}

// watchers
watch(
    [projectId, geneGridApi],
    async ([newId, api]) => {
        if (!newId || !api) return;

        if (insertedGeneProjects.value.has(newId)) return

        insertedGeneProjects.value.add(newId)

        console.log('[Watcher: GeneGrid] Project ID or Grid API changed:', newId);
        try {
            await fetchProject(newId)
            console.log('[Watcher: GeneGrid] Project data fetched')

            api.setGridOption('serverSideDatasource', geneDatasource)
            console.log('[Watcher: GeneGrid] Datasource set')

            api.refreshServerSide({ purge: true })
            console.log('[Watcher: GeneGrid] grid refreshed')
        } catch (error) {
            console.error('[Watcher: GeneGrid] Error during update:', error);
        }
    },
    { immediate: true }
);

watch(
    [projectId, exonGridApi],
    async ([newId, api]) => {
        if (!newId || !api) return;

        if (insertedExonProjects.value.has(newId)) return

        insertedExonProjects.value.add(newId)

        console.log('[Watcher: ExonGrid] Project ID or Grid API changed:', newId);
        try {
            api.setGridOption('serverSideDatasource', exonDatasource)
            console.log('[Watcher: ExonGrid] Datasource set')

            api.refreshServerSide({ purge: true })
            console.log('[Watcher: ExonGrid] Grid refreshed')
        } catch (error) {
            console.error('[Watcher: ExonGrid] Error during update:', error);
        }
    },
    { immediate: true }
)

// grid options
const BASE_GRID_OPTIONS: GridOptions = {
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
        wrapText: false,
        autoHeight: false,
    },
    pagination: true,
    animateRows: false,
}

const projectGridOptions: GridOptions = {
    ...BASE_GRID_OPTIONS,
    columnDefs: projectColumnDefs,
    rowModelType: 'clientSide',
    onGridReady: onProjectGridReady,
}

const geneGridOptions: GridOptions = {
    ...BASE_GRID_OPTIONS,
    columnDefs: geneColumnDefs,
    rowModelType: 'serverSide',
    onGridReady: onGeneGridReady,
}

const exonGridOptions: GridOptions = {
    ...BASE_GRID_OPTIONS,
    columnDefs: exonColumnDefs,
    rowModelType: 'serverSide',
    onGridReady: onExonGridReady,
}

</script>

<template>

    <button class="collapsible" @click="toggleProject">
        {{ isProjectVisible ? 'Metadata Table' : 'Metadata Table' }}
    </button>

    <div class="content" :style="{ display: isProjectVisible ? 'block' : 'none' }">
        <AgGridVue class="ag-theme-balham ag-grid-wrapper" :rowData="project" :gridOptions="projectGridOptions"
            :theme="mdTheme" />
    </div>

    <button class="collapsible" @click="toggleGene">
        {{ isGeneVisible ? 'Gene Table' : 'Gene Table' }}
    </button>

    <div class="content" :style="{ display: isGeneVisible ? 'block' : 'none' }">
        <AgGridVue class="ag-theme-balham ag-grid-wrapper" :gridOptions="geneGridOptions" :theme="mdTheme" />
    </div>

    <button class="collapsible" @click="toggleExon">
        {{ isGeneVisible ? 'Exon Table' : 'Exon Table' }}
    </button>

    <div class="content" :style="{ display: isExonVisible ? 'block' : 'none' }">
        <AgGridVue class="ag-theme-balham ag-grid-wrapper" :gridOptions="exonGridOptions" :theme="mdTheme" />
    </div>

</template>

<style scoped>
.collapsible {
    background-color: #eee;
    color: #444;
    cursor: pointer;
    padding: 10px;
    width: 80vw;
    border: none;
    text-align: left;
    outline: none;
    font-size: 16px;
    margin-top: 1rem;
}

.active,
.collapsible:hover {
    background-color: #ccc;
}

.content {
    display: none;
    overflow: hidden;
    transition: max-height 0.2s ease-out;
}

.ag-grid-wrapper {
    height: 50vh;
    width: 80vw;
}
</style>
