export function invokeAddService(data: CreateServiceDto): Promise<ApiResponse<number>> {
  return window.electron.ipcRenderer.invoke('service:create', data)
}

export function invokeGetAllServices(): Promise<ApiResponse<Service[]>> {
  return window.electron.ipcRenderer.invoke('service:findAll')
}

export function invokeGetServiceById(id: number): Promise<ApiResponse<Service | undefined>> {
  return window.electron.ipcRenderer.invoke('service:findById', id)
}

export function invokeGetServicesByGroupId(groupId: number): Promise<ApiResponse<Service[]>> {
  return window.electron.ipcRenderer.invoke('service:findByGroupId', groupId)
}

export function invokeUpdateService(
  id: number,
  data: Partial<CreateServiceDto>
): Promise<ApiResponse<number>> {
  return window.electron.ipcRenderer.invoke('service:update', id, data)
}

export function invokeDeleteService(id: number): Promise<ApiResponse<number>> {
  return window.electron.ipcRenderer.invoke('service:delete', id)
}

export default {
  invokeAddService,
  invokeGetAllServices,
  invokeGetServiceById,
  invokeGetServicesByGroupId,
  invokeUpdateService,
  invokeDeleteService
}
