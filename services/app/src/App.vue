<script setup lang="ts">
import { provide } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { SidebarProvider } from '@/components/ui/sidebar'
import { AllCommunityModule, ModuleRegistry, themeBalham } from 'ag-grid-community';
import { ServerSideRowModelModule } from 'ag-grid-enterprise'

ModuleRegistry.registerModules([AllCommunityModule, ServerSideRowModelModule])

const mdTheme = themeBalham.withParams({ accentColor: '#611f69' });

provide('mdTheme', mdTheme);

</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <main>
      <RouterView />
    </main>
  </SidebarProvider>
</template>
