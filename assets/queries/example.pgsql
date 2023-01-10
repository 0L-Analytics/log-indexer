select * 
from validatorlog
where log_type = 'ERROR'
AND log_context = '[state-sync]'
LIMIT 10;
