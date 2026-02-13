<template>
    <div class="govespend-container">
        <h1>Despesas Públicas</h1>

        <div v-if="loading" class="status-message">
            Carregando dados...
        </div>

        <div v-else-if="error" class="error-message">
            {{ error }}
        </div>

        <div v-else class="table-responsive">
            <table class="despesas-table">
                <thread>
                    <tr>
                        <th style="width: 10%;">ID</th>
                        <th style="width: 50%;">Órgão</th>
                        <th class="text-right" style="width: 20%;">Valor Pago</th>
                        <th class="text-right" style="width: 20%;">Valor Empenhado</th>
                    </tr>
                </thread>
                <tbody>
                    <tr v-for="despesa in despesas" :key="despesa.id_orgao">
                        <td>{{ despesa.id_orgao }}</td>
                        <td>{{ despesa.nome_orgao }}</td>
                        <td class="text-right">{{ formatCurrency(despesa.valor_pago) }}</td>
                        <td class="text-right">{{ formatCurrency(despesa.valor_empenhado) }}</td>
                        <td style="text-align: center;">
                            <button class="btn-detalhes" @click="openDetails(despesa.id_orgao)">
                                Ver Detalhes
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <despesa-detail
            v-if="selectedId"
            :id="selectedId"
            @close="selectedId = null"
        />

    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import DespesaDetail from './DespesaDetail.vue';

defineOptions({
    name: 'DespesasList'
});

const despesas = ref([]);
const loading = ref(true);
const error = ref(null);
const selectedId = ref(null);

const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
};

const openDetails = (id) => {
    selectedId.value = id;
};

onMounted(async () => {
    try {
        const response = await axios.get('http://localhost:8000/despesas/');
        despesas.value = response.data;
    } catch (err) {
        console.error("Falha ao buscar despesas:", err);
        error.value = "Não foi possível carregar os dados da API.";
    } finally {
        loading.value = false;
    }
});
</script>

<style scoped>
.govespend-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
}

h1 {
    color: #2c3e50;
    margin-bottom: 20px;
}

.status-message {
    color: #666;
    font-style: italic;
}

.error-message {
    color: #e74c3c;
    font-weight: bold;
}

.despesas-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    table-layout: fixed;
}

.despesas-table th,
.despesas-table td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.despesas-table th {
    background-color: #42b983;
    color: white;
}

.despesas-table tr:nth-child(even) {
    background-color: #f9f9f9;
}

.despesas-table tr:hover {
    background-color: #f1f1f1;
}

.text-right {
    text-align: right !important;
}

.btn-detalhes {
    background-color: #34495e;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
}

.btn-detalhes:hover {
    background-color: #2c3e50;
}
</style>