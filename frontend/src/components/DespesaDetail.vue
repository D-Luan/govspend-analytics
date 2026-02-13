<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content">
            <button class="close-btn" @click="$emit('close')">&times;</button>

            <h2>Detalhes do Órgão</h2>

            <div v-if="loading" class="status">Carregando detalhes...</div>
            <div v-else-if="error" class="error">{{ error }}</div>

            <div v-else-if="despesa" class="detail-grid">
                <div class="field">
                    <label>ID do Órgão:</label>
                    <span>{{ despesa.id_orgao }}</span>
                </div>
                
                <div class="field">
                    <label>Nome do Órgão:</label>
                    <span>{{ despesa.nome_orgao }}</span>
                </div>

                <div class="field highlight">
                    <label>Valor Pago:</label>
                    <span>{{ formatCurrency(despesa.valor_pago) }}</span>
                </div>

                <div class="field highlight">
                    <label>Valor Empenhado:</label>
                    <span>{{ formatCurrency(despesa.valor_empenhado) }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue';
    import axios from 'axios';

    const props = defineProps({
        id: {
            type: Number,
            required: true
        }
    });

    const emit = defineEmits(['close']);

    const despesa = ref(null);
    const loading = ref(true);
    const error = ref(null);

    const formatCurrency = (value) => {
        if (value === null || value === undefined) return 'R$ 0,00';
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);   
    };

    onMounted(async () => {
        try {
            const response = await axios.get(`http://localhost:8000/despesas/${props.id}`);
            despesa.value = response.data;
        } catch (err) {
            console.error(err);
            error.value = "Erro ao carregar detalhes.";
        } finally {
            loading.value = false;
        }
    });
</script>

<style scoped>
    .modal-overlay {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-content {
        background: white;
        padding: 30px;
        border-radius: 8px;
        width: 90%;
        max-width: 500px;
        position: relative;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .close-btn {
        position: absolute;
        top: 10px;
        right: 15px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
    }

    .detail-grid {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-top: 20px;
    }

    .field {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }

    .field label {
        font-weight: bold;
        color: #555;
    }

    .highlight span {
        color: #42b983;
        font-weight: bold;
    }

    .error { color: red; }
    .status { color: gray; font-style: italic; }
</style>