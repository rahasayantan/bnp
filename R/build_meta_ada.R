## wd etc ####
require(readr)
require(ada)
require(stringr)
require(Metrics)
require(caret)

dataset_version <- "16v2k25"
seed_value <- 1901
model_type <- "ada"
todate <- str_replace_all(Sys.Date(), "-","")

## functions ####

msg <- function(mmm,...)
{
  cat(sprintf(paste0("[%s] ",mmm),Sys.time(),...)); cat("\n")
}

# wrapper around logloss preventing Inf/-Inf for 1/0 values
log_loss <- function(actual, predicted, cutoff = 1e-15)
{
  predicted <- pmax(predicted, cutoff)
  predicted <- pmin(predicted, 1- cutoff)
  return(logLoss(actual,predicted))
}

## data ####
# read actual data
xtrain <- read.csv(paste("../input2/xtrain_",dataset_version,".csv", sep = ""))
xtest <- read.csv(paste("../input2/xtest_",dataset_version,".csv", sep = ""))
y <- xtrain$target; 
xtrain$target <- NULL
id_train <- xtrain$ID
id_test <- xtest$ID
xtrain$ID <- xtest$ID <- NULL

# division into folds: 5-fold
xfolds <- read_csv("../input/xfolds.csv"); xfolds$fold_index <- xfolds$fold5
xfolds <- xfolds[,c("ID", "fold_index")]
nfolds <- length(unique(xfolds$fold_index))

## fit models ####
# parameter grid
param_grid <- expand.grid(type = c("real", "gentle"),
                          iter = c(50,50),
                          nu = c(0.01, 0.05, 0.1),
                          bagfrac = c(0.1, 0.9))
write.csv(param_grid, 
          paste('../meta_parameters2/D', dataset_version, '_M',model_type,
                '_',todate,'.csv',sep = ""),
          row.names = F, quote = F)

# storage structures 
mtrain <- array(0, c(nrow(xtrain), nrow(param_grid)))
mtest <- array(0, c(nrow(xtest), nrow(param_grid)))

# loop over parameters
for (ii in 1:nrow(param_grid))
{
  
  # loop over folds 
  for (jj in 1:nfolds)
  {
    isTrain <- which(xfolds$fold_index != jj)
    isValid <- which(xfolds$fold_index == jj)
    x0 <- xtrain[isTrain,]; x1 <- xtrain[isValid,]
    y0 <- y[isTrain]; y1 <- y[-isTrain]
    
    ada.model <- ada(x = x0, y= y0, 
                     loss=  "exponential", type = as.character(param_grid$type[ii]),
                     iter = param_grid$iter[ii], nu = param_grid$nu[ii], 
                     bag.frac = param_grid$bagfrac[ii],
                     verbose = T, rpart.control(maxdepth=1,cp=-1,minsplit=0,xval=0))
    
    pred_valid <- predict(ada.model, x1, type = "probs")
    print(log_loss(y1, pred_valid))
    mtrain[isValid,ii] <- pred_valid
  }
  
  # full version 
  mars.model <- earth(x = xtrain, y = factor(y), degree = param_grid$deg[ii], glm=list(family=binomial))
  
  pred_full <- predict(mars.model, xtest, type = "response")
  mtest[,ii] <- pred_full
  msg(ii)
}

## store complete versions ####
mtrain <- data.frame(mtrain)
mtest <- data.frame(mtest)
colnames(mtrain) <- colnames(mtest) <- paste(model_type, 1:ncol(mtrain), sep = "")
mtrain$ID <- id_train
mtest$ID <- id_test
mtrain$TARGET <- y

# Remove any linear combos.
# trim linearly dependent ones 
print(paste("Pre linear combo trim size ", dim(mtrain)[2]))
flc <- findLinearCombos(mtrain)
if (length(flc$remove))
{
  mtrain <- mtrain[,-flc$remove]
  mtest <- mtest[,-flc$remove]
}
print(paste(" Number of cols after linear combo extraction:", dim(mtrain)[2]))



write_csv(mtrain, path = paste("../metafeatures2/prval_",model_type,"_", todate, "_data", dataset_version, "_seed", seed_value, ".csv",sep = "" ))
write_csv(mtest, path = paste("../metafeatures2/prfull_",model_type,"_", todate, "_data", dataset_version, "_seed", seed_value, ".csv",sep = "" ))


