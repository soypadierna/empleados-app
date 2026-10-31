"use strict";

const $ = (id) => document.getElementById(id);
let empleados = [];
let idSel = null;
let fuenteActual = "json";
let tBusqueda = null;
let tEstado = null;

async function llamar(metodo, ...args) {
  try {
    return await window.pywebview.api[metodo](...args);
  } catch (e) {
    return { ok: false, data: null, error: "Error de comunicación: " + e };
  }
}

function estado(msg, tipo = "ok") {
  const el = $("lblEstado");
  el.textContent = msg;
  el.className = "estado " + tipo;
  clearTimeout(tEstado);
  if (tipo !== "error") {
    tEstado = setTimeout(() => { el.textContent = "Listo."; el.className = "estado"; }, 5000);
  }
}

async function cargar() {
  const texto = $("txtBuscar").value.trim();
  const r = texto ? await llamar("buscar", texto) : await llamar("listar");
  if (!r.ok) return estado(r.error, "error");
  empleados = r.data;
  pintarTabla();
}

function pintarTabla() {
  const tbody = $("grdEmpleados").tBodies[0];
  tbody.replaceChildren();
  if (empleados.length === 0) {
    const tr = tbody.insertRow();
    const td = tr.insertCell();
    td.colSpan = 7;
    td.className = "vacio";
    td.textContent = "Sin resultados.";
  }
  for (const e of empleados) {
    const tr = tbody.insertRow();
    tr.dataset.id = e.IdEmpleado;
    for (const campo of ["IdEmpleado", "StrNombre", "NumDocumento", "StrDireccion",
                         "StrTelefono", "StrEmail", "DtmIngreso"]) {
      const td = tr.insertCell();
      td.textContent = e[campo];
      td.title = e[campo];
    }
    tr.addEventListener("click", () => seleccionar(e));
  }
  $("lblConteo").textContent = `${empleados.length} empleado(s)`;
  marcarFila();
}

function marcarFila() {
  for (const tr of $("grdEmpleados").tBodies[0].rows) {
    tr.classList.toggle("sel", Number(tr.dataset.id) === idSel);
  }
}

function seleccionar(e) {
  idSel = e.IdEmpleado;
  $("txtId").value = e.IdEmpleado;
  $("txtNombre").value = e.StrNombre;
  $("txtDocumento").value = e.NumDocumento;
  $("txtDireccion").value = e.StrDireccion;
  $("txtTelefono").value = e.StrTelefono;
  $("txtEmail").value = e.StrEmail;
  $("dtpIngreso").value = e.DtmIngreso;
  $("btnEliminar").disabled = false;
  marcarFila();
}

function limpiar() {
  idSel = null;
  $("frmEmpleado").reset();
  $("txtId").value = "";
  $("btnEliminar").disabled = true;
  marcarFila();
  $("txtNombre").focus();
}

async function guardar(ev) {
  ev.preventDefault();
  const datos = {
    StrNombre: $("txtNombre").value.trim(),
    NumDocumento: $("txtDocumento").value.trim(),
    StrDireccion: $("txtDireccion").value.trim(),
    StrTelefono: $("txtTelefono").value.trim(),
    StrEmail: $("txtEmail").value.trim(),
    DtmIngreso: $("dtpIngreso").value,
  };
  const nuevo = idSel === null;
  const r = nuevo ? await llamar("agregar", datos) : await llamar("editar", idSel, datos);
  if (!r.ok) return estado(r.error, "error");
  await cargar();
  seleccionar(r.data);
  estado(nuevo ? `Empleado agregado (ID ${r.data.IdEmpleado}).` : "Empleado actualizado.");
}

async function eliminar() {
  if (idSel === null) return;
  if (!confirm(`¿Eliminar a "${$("txtNombre").value}"? Esta acción no se puede deshacer.`)) return;
  const r = await llamar("eliminar", idSel);
  if (!r.ok) return estado(r.error, "error");
  limpiar();
  await cargar();
  estado("Empleado eliminado.");
}

async function cambiarFuente() {
  const nueva = $("cmbFuente").value;
  const r = await llamar("cambiar_fuente", nueva);
  if (!r.ok) {
    $("cmbFuente").value = fuenteActual;
    return estado(r.error, "error");
  }
  fuenteActual = nueva;
  limpiar();
  await cargar();
  estado(`Fuente cambiada a ${nueva.toUpperCase()}.`);
}

async function exportar() {
  const r = await llamar("exportar_csv");
  if (!r.ok) return estado(r.error, "error");
  estado(r.data ? `CSV exportado: ${r.data}` : "Exportación cancelada.");
}

$("frmEmpleado").addEventListener("submit", guardar);
$("btnNuevo").addEventListener("click", limpiar);
$("btnEliminar").addEventListener("click", eliminar);
$("btnExportar").addEventListener("click", exportar);
$("cmbFuente").addEventListener("change", cambiarFuente);
$("txtBuscar").addEventListener("input", () => {
  clearTimeout(tBusqueda);
  tBusqueda = setTimeout(cargar, 200);
});
window.addEventListener("pywebviewready", () => { limpiar(); cargar(); });